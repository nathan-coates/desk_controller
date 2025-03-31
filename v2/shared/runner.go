package shared

import "time"

type Job struct {
	job      func()
	stopChan chan struct{}
	interval time.Duration
}
type Runner struct {
	jobs []*Job
}

func NewJob(job func(), duration time.Duration) *Job {
	return &Job{
		job:      job,
		interval: duration,
	}
}

func NewRunner() *Runner {
	return &Runner{
		jobs: make([]*Job, 0),
	}
}

func (r *Runner) AddJob(job *Job) {
	r.jobs = append(r.jobs, job)
}

func (r *Runner) Run() {
	for _, job := range r.jobs {
		job.stopChan = make(chan struct{})
		go func() {
			for {
				select {
				case <-job.stopChan:
					return
				case <-time.After(job.interval):
					job.job()
				}
			}
		}()
	}
}

func (r *Runner) Stop() {
	for _, job := range r.jobs {
		job.stopChan <- struct{}{}
		close(job.stopChan)
	}
}
